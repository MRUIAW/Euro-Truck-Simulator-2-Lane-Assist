import Image from "next/image"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from "@/components/ui/accordion"
import {
	AlertDialog,
	AlertDialogAction,
	AlertDialogCancel,
	AlertDialogContent,
	AlertDialogDescription,
	AlertDialogFooter,
	AlertDialogHeader,
	AlertDialogTitle,
	AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { toast } from "sonner"
import useSWR from "swr"
import { mutate } from "swr"
import { CheckUsernameAvailability, Register, Login } from "@/pages/account"
import { useState } from "react"
import { set } from "date-fns"
import { CircleCheckBig, LogIn } from "lucide-react"
import darkPromo from "@/assets/promo_dark.png"
import lightPromo from "@/assets/promo_light.png"
import { useTheme } from "next-themes"

export function Authentication({ onLogin } : { onLogin: (token:string) => void }) {
	const [username, setUsername] = useState("")
	const [usernameAvailable, setUsernameAvailable] = useState(false)
	const [password, setPassword] = useState("")
	const [passwordRepeat, setPasswordRepeat] = useState("")
	const [isDialogOpen, setIsDialogOpen] = useState(false);
	const { theme, setTheme } = useTheme()
	const [passwordState, setPasswordState] = useState({
		uppercase: false,
		lowercase: false,
		length: 0,
		eightCharsOrGreater: false,
	});


	const handleGuestLogin = () => {
		toast.success("Logged in as a guest")
		onLogin("guest")
	}

	const handleLogin = async () => {
		if (usernameAvailable) {
			setIsDialogOpen(true)
		} else {
			const token = await Login(username, password)
			if (token) {
				toast.success("Logged in")
				onLogin(token)
			} else {
				toast.error("Password for " + username + " is incorrect")
			}
		}
	}	

	const handleDialogClose = async (confirmed: boolean) => {
		setIsDialogOpen(false)
		if (confirmed) {
			if (password !== passwordRepeat) {
				toast.error("Passwords do not match")
				return
			}
			if (!passwordState.uppercase || !passwordState.lowercase || !passwordState.eightCharsOrGreater) {
				toast.error("Password doesn't meet the requirements")
				return
			}
			const token = await Register(username, password)
			if (token) {
				toast.success("Account created")
				onLogin(token)
			} else {
				toast.error("Failed to create account")
			}
		}
	}

	const onUsernameChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const username = e.target.value
		setUsername(username)
		if (await CheckUsernameAvailability(username)) {
			setUsernameAvailable(true)
		} else if (username === "Username") {
			setUsernameAvailable(true)
		} else {
			setUsernameAvailable(false)
		}
	}

	const onPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const newPassword = e.target.value; // -> created const not to use 'e.target.value' two times
		setPassword(newPassword)
		
		// set the new password state
		setPasswordState(getPasswordStrength(newPassword))
	}

	const onPasswordRepeatChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setPasswordRepeat(e.target.value)
	}

	function passwordsMatch() {
		if (passwordRepeat === "" || password === "") {
			return true;
		}
		return password === passwordRepeat;
	}

	function getPasswordStrength(password: string) {
		// Define regular expressions for different criteria
		const lowercaseRegex = /[a-z]/; // all lowercase chars
		const uppercaseRegex = /[A-Z]/; // all uppercase chars
		
		// Define passwordMeter to check which symbols/chars are in the password
		const passwordMeter = {
			uppercase: Boolean(password.match(uppercaseRegex)),
			lowercase: Boolean(password.match(lowercaseRegex)),
			length: password.length,
			eightCharsOrGreater: password.length >= 8,
		  }
		
		  // return it
		return passwordMeter
	}

	return (
	<div className="w-full lg:grid lg:grid-cols-2 h-full">
		<div  className="flex items-center justify-center h-[calc(100vh-72px)]">
			<div className="mx-auto grid w-[350px] gap-6">
				<div className="grid gap-2 text-center">
					<h1 className="text-3xl font-bold">{usernameAvailable ? "Signup" : "Login"}</h1>
					<p className="text-balance text-muted-foreground">
						Please login or sign up to access the application.
					</p>
				</div>
				<div className="grid gap-4">
					<div className="grid gap-2">
						<div className="flex items-center">
							<Label htmlFor="email">Username</Label>
							<p className="ml-auto text-sm flex gap-1 items-center text-zinc-500">
								{usernameAvailable ? (
									<CircleCheckBig className="w-4 h-4" />
								) : (
									<LogIn className="w-4 h-4" />
								)}
							</p>
						</div>
						<Input
							id="email"
							type="text"
							placeholder="Username"
							required
							onChange={onUsernameChange}
						/>
					</div>
					<div className="grid gap-2">
						<div className="flex items-center">
							<Label htmlFor="password">Password</Label>
						</div>
						<div className="flex gap-2">
							<Input id="password" type="password" placeholder="Password" required onChange={onPasswordChange} />
							<Input id="passwordRepeat" type="password" placeholder="Repeat password" required onChange={onPasswordRepeatChange} disabled={!usernameAvailable}
								className={passwordsMatch() ? "" : "border-red-700 focus:border-2"}
							/>
						</div>
					</div>
					{usernameAvailable ? (
						<>
							<AlertDialog>
								<AlertDialogTrigger>
									<Button type="submit" className="w-full" onClick={handleLogin}>
										Login
									</Button>
								</AlertDialogTrigger>
								<AlertDialogContent>
									<AlertDialogHeader>
										<AlertDialogTitle>Confirm</AlertDialogTitle>
										<AlertDialogDescription>
											This will create a new account.
										</AlertDialogDescription>
									</AlertDialogHeader>
									<AlertDialogFooter>
										<AlertDialogCancel onClick={() => handleDialogClose(false)}>Cancel</AlertDialogCancel>
										<AlertDialogAction onClick={() => handleDialogClose(true)}>Continue</AlertDialogAction>
									</AlertDialogFooter>
								</AlertDialogContent>
							</AlertDialog>
						</>
					) : (
						<Button type="submit" className="w-full" onClick={handleLogin}>
							{usernameAvailable ? "Create Account" : "Login"}
						</Button>
					)}
					<Button variant="outline" className="w-full" onClick={handleGuestLogin}>
						Use a Guest account
					</Button>
					<Accordion type="single" collapsible className="w-[350px] place-self-center" value={usernameAvailable ? passwordState.uppercase && passwordState.lowercase && passwordState.eightCharsOrGreater ? "" : "item-1" : ""}>
						<AccordionItem value="item-1">
							<AccordionTrigger className="w-[400px]"><p
								className={!usernameAvailable ? "text-zinc-500 transition-colors ease-in-out duration-500" : passwordState.uppercase && passwordState.lowercase && passwordState.eightCharsOrGreater ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}
								>Password Requirements</p></AccordionTrigger>
							<AccordionContent className="flex justify-between pr-0 w-full p-4 pt-0">
								<p style={{fontSize: '0.9em'}}
									className={passwordState.uppercase ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}> {'Uppercase'} </p>
								<p style={{fontSize: '0.9em'}}
									className={passwordState.lowercase ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}> {'Lowercase'} </p>
								<p style={{fontSize: '0.9em'}}
									className={passwordState.eightCharsOrGreater ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}> {'Characters [' + passwordState.length + '/8]'} </p>

								
							</AccordionContent>
						</AccordionItem>
					</Accordion>
				</div>
				<div className="mt-4 text-center text-sm">
					<p className="text-muted-foreground">Don't have an account? Just type in your desired username and password and we will create one for you.</p>
				</div>
			</div>
		</div>
		<div className="hidden rounded-xl h-full lg:flex w-full">
			{usernameAvailable ? (
			<>
				<Separator orientation='vertical' />
				<div className="w-full h-full p-20 animate-in fade-in-5 duration-500">
					<Accordion type="single" collapsible className="place-self-center">
						<AccordionItem value="item-1">
							<AccordionTrigger className="w-[400px]">Is it free?</AccordionTrigger>
							<AccordionContent>
								<p>Yes, all features are free to use.</p> 
								<p>With, or without an account.</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-2">
							<AccordionTrigger className="w-[400px]">Do you collect private data?</AccordionTrigger>
							<AccordionContent>
								<p>No, we do not collect any private data out of principle. I do not want to handle any private data of users, that is too big of a responsibility for me.</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-3">
							<AccordionTrigger className="w-[400px]">Why do I need an account?</AccordionTrigger>
							<AccordionContent>
								<p>You do not need an account to use the app. An account is only needed for the following <p className="font-bold inline">free</p> features.</p>
								<ul className="pt-2">
									<li>• Cloud settings saving</li>
									<li>• Developer comments on feedback and support requests</li>
									<li>• Personal data portal for ETS2 data (see past deliveries etc...)</li>
								</ul>
								<p className="pt-2">The app will still collect the ETS2 data without an account. But it will be appended to the public anonymous data portal instead of being tied to your account.</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-4">
							<AccordionTrigger className="w-[400px]">How do I delete my account?</AccordionTrigger>
							<AccordionContent>
								<p>This has not yet been implemented in app, for now please contact me on discord @Tumppi066 or email to <a href="mailto:contact@tumppi066.fi" className="underline">contact@tumppi066.fi</a></p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-5">
							<AccordionTrigger className="w-[400px]">What data do you collect then?</AccordionTrigger>
							<AccordionContent>
								<p>We the following. Please note that this list includes everything that the app will collect "in the worst case". Most of these can be turned off in the settings!</p>
								<ul className="pt-2">
									<li>• Ping to the central server every 60s</li>
									<li>• App settings</li>
									<li>• App logs (on crash)</li>
									<li>• ETS2 API data (see <a href="https://github.com/RenCloud/scs-sdk-plugin?tab=readme-ov-file#telemetry-fields-and-the-c-object" target="_blank" className="underline"> the github repo</a>)</li>
								</ul>
								<p className="pt-2">None of the data we collect can be traced back to you. The server doesn't log IPs, ETS2 usernames etc...</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-6">
							<AccordionTrigger className="w-[400px]">How are my login details stored on my device?</AccordionTrigger>
							<AccordionContent>
								<p>The app doesn't actually store your login details on device. In fact nowhere in the pipeline is your password stored as plain text. Instead the server provides your device with a login token.</p>
								<p className="pt-1">This token is then stored in your browser's local storage. It is important to note that, even though this does protect your password, if someone get's hold of said token, they can log into your account.</p>
							</AccordionContent>
						</AccordionItem>
					</Accordion>
				</div>
			</>
			) : 
			(
				<Image
					src={theme === "dark" ? darkPromo : lightPromo}
					alt="ETS2LA Promo"
					className="rounded-xl h-full object-left object-cover animate-in fade-in-5 duration-500"
				/>
			)}
		</div>
	</div>
)
}